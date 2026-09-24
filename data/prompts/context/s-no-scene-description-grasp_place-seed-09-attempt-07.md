## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3770 | 0.77 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1636 | 0.36 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1002 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1455 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0380 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.377) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_object
  target_entity: object
  weight: 0.6
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_lift_check
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_lift_check
    when: before_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_lift_check, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_lift_check, when=before_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.377
- **task_score** (E): 0.767
- **fitness_score**: 0.847  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1097 |
| descend_to_grasp | 1.00 | 1.00 | 0.1422 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift | 0.33 | 1.00 | 0.0957 |
| transport | 0.67 | 1.00 | 0.2572 |
| descend_to_place | 1.00 | 0.33 | 0.0477 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.055)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.139 | 0.185 |
| lift | lift | 0.33 / step_budget | (0.502, -0.016, 0.045)→(0.507, -0.016, 0.141) | (0.515, -0.016, 0.026)→(0.517, -0.016, 0.114) | 0.270→0.237 | 1.00 / 28.667 | 0.102 | 0.399 |
| transport | approach | 0.67 / step_budget | (0.507, -0.016, 0.141)→(0.607, 0.160, 0.292) | (0.517, -0.016, 0.114)→(0.612, 0.159, 0.257) | 0.237→0.093 | 1.00 / 15.333 | 0.157 | 0.183 |
| descend_to_place | descend | 1.00 / step_budget | (0.607, 0.160, 0.292)→(0.612, 0.173, 0.250) | (0.612, 0.159, 0.257)→(0.621, 0.163, 0.166) | 0.093→0.041 | 0.33 / 7.333 | 0.044 | 0.234 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.863
- phase_score: 0.348
- phase_breakdown.lift_object_score: 0.429
- phase_breakdown.reach_object_score: 0.220
- phase_breakdown.place_object_score: 0.329
- grasp_place_fitness: 0.895

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.895
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.863
- **Median Q (composite search score)**: 0.401
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.286


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15319,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.09838,"descend_to_grasp.descend_speed":0.0573,"descend_to_place.descend_speed":0.04147,"descend_to_place.place_z_offset":0.08878,"lift.lift_height":0.12217,"lift.lift_speed":0.13169,"transport.speed":0.04706},"optimized_scores":{"best_composite_score":0.30453,"best_fitness_score":0.77453,"best_task_score":0.62209},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.53508,-0.02027,-0.00127],"force_p95":0.21932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40385,"mean_force":0.06223,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52121,-0.02043,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8947.0,"contact_point_centroid":[0.52748,-0.00154,0.08459],"force_p95":0.0943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26898,"mean_force":0.06157,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52437,-0.02048,0.08204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8984.0,"contact_point_centroid":[0.52745,-0.03947,0.08458],"force_p95":0.09655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26587,"mean_force":0.06165,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52443,-0.02048,0.08234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11467.0,"contact_point_centroid":[0.56564,0.09523,0.21594],"force_p95":0.12747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23456,"mean_force":0.08153,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5597,0.07652,0.21538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.60189,0.19782,0.30216],"force_p95":0.22494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22791,"mean_force":0.2009,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59448,0.18306,0.30959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12834.0,"contact_point_centroid":[0.56725,0.06328,0.22053],"force_p95":0.09853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22347,"mean_force":0.07333,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56143,0.08179,0.22006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.60103,0.16969,0.30497],"force_p95":0.15971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21595,"mean_force":0.06587,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59486,0.1844,0.30872]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02122,-0.00207],"force_p95":0.14267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19356,"mean_force":0.12839,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52373,-0.02047,0.0459]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51262,-0.00821,0.24961]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52821,-0.01886,0.12652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5000.0,"contact_point_centroid":[0.52349,-0.00128,0.04746],"force_p95":0.06693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1006,"mean_force":0.04329,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52255,-0.02045,0.04453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.52353,-0.03972,0.04631],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07299,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52255,-0.02045,0.04453]}],"total_contact_groups":12},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61857,0.18582,0.15046],"final_tcp_position":[0.60269,0.20935,0.29474],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.40385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5273,-0.01722,0.19684],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53126,-0.02059,0.05501],"tcp_start":[0.5273,-0.01722,0.19684],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02073,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13994,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11729.0,"raw_peak_contact_force":0.19356,"tcp_end":[0.52252,-0.02045,0.04449],"tcp_start":[0.53126,-0.02059,0.05501],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.54557,-0.02062,0.11014],"object_pos_start":[0.53695,-0.02073,0.02572],"object_to_goal_dist_end":0.27448,"object_to_goal_dist_start":0.31645,"object_z_max":0.11001,"peak_contact_force":0.08647,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18111.0,"raw_peak_contact_force":0.40385,"subtask_id":"lift_object","tcp_end":[0.53179,-0.02063,0.13446],"tcp_start":[0.52252,-0.02045,0.04449],"tcp_to_object_dist_end":0.02795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60067,0.18115,0.27527],"object_pos_start":[0.54557,-0.02062,0.11014],"object_to_goal_dist_end":0.08288,"object_to_goal_dist_start":0.27448,"object_z_max":0.27532,"peak_contact_force":0.22019,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24301.0,"raw_peak_contact_force":0.23456,"tcp_end":[0.59448,0.18299,0.30958],"tcp_start":[0.53179,-0.02063,0.13446],"tcp_to_object_dist_end":0.03491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.61857,0.18582,0.15046],"object_pos_start":[0.60067,0.18115,0.27527],"object_to_goal_dist_end":0.0712,"object_to_goal_dist_start":0.08288,"object_z_max":0.27527,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":136.0,"raw_peak_contact_force":0.22791,"subtask_id":"place_object","tcp_end":[0.60269,0.20935,0.29474],"tcp_start":[0.59448,0.18299,0.30958],"tcp_to_object_dist_end":0.14704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89905,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.15006,"descend_to_grasp.descend_speed":0.01864,"descend_to_place.descend_speed":0.1102,"descend_to_place.place_z_offset":0.03662,"lift.lift_height":0.18487,"lift.lift_speed":0.05954,"transport.speed":0.02301},"optimized_scores":{"best_composite_score":0.42523,"best_fitness_score":0.89523,"best_task_score":0.863},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.54197,-0.02764,-0.00121],"force_p95":0.23265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4149,"mean_force":0.07313,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52897,-0.02795,0.04561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18673.0,"contact_point_centroid":[0.53208,-0.00882,0.09032],"force_p95":0.08272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28283,"mean_force":0.05482,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53082,-0.02794,0.08844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19692.0,"contact_point_centroid":[0.53232,-0.047,0.09263],"force_p95":0.076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27773,"mean_force":0.05173,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53103,-0.02794,0.09084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1203.0,"contact_point_centroid":[0.62812,0.17535,0.26577],"force_p95":0.15848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25201,"mean_force":0.10956,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62709,0.15743,0.2702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1386.0,"contact_point_centroid":[0.62837,0.13916,0.26625],"force_p95":0.16336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24905,"mean_force":0.10739,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62708,0.1574,0.27054]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02912,-0.00211],"force_p95":0.15215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21236,"mean_force":0.13111,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53194,-0.02805,0.04528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11948.0,"contact_point_centroid":[0.57715,0.074,0.21168],"force_p95":0.1287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15128,"mean_force":0.08022,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57468,0.05518,0.21344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.5316,-0.00882,0.04687],"force_p95":0.07049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14449,"mean_force":0.04527,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53074,-0.02801,0.04387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15368.0,"contact_point_centroid":[0.57663,0.03668,0.21254],"force_p95":0.11066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14419,"mean_force":0.06199,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57465,0.05513,0.21338]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51621,-0.01146,0.24859]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53578,-0.02596,0.12667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4967.0,"contact_point_centroid":[0.53184,-0.04726,0.04563],"force_p95":0.07228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07384,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53074,-0.02801,0.04387]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62516,0.15945,0.19691],"final_tcp_position":[0.62873,0.16106,0.23224],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.4149,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53452,-0.02387,0.19556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53954,-0.02825,0.05464],"tcp_start":[0.53452,-0.02387,0.19556],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02824,0.0256],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26045,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14891,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11504.0,"raw_peak_contact_force":0.21236,"tcp_end":[0.53071,-0.02801,0.04383],"tcp_start":[0.53954,-0.02825,0.05464],"tcp_to_object_dist_end":0.02351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54103,-0.02816,0.11297],"object_pos_start":[0.54555,-0.02824,0.0256],"object_to_goal_dist_end":0.22316,"object_to_goal_dist_start":0.26045,"object_z_max":0.11286,"peak_contact_force":0.09252,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38595.0,"raw_peak_contact_force":0.4149,"subtask_id":"lift_object","tcp_end":[0.5355,-0.02801,0.13896],"tcp_start":[0.53071,-0.02801,0.04383],"tcp_to_object_dist_end":0.02657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63022,0.1528,0.27443],"object_pos_start":[0.54103,-0.02816,0.11297],"object_to_goal_dist_end":0.0983,"object_to_goal_dist_start":0.22316,"object_z_max":0.27428,"peak_contact_force":0.12787,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27316.0,"raw_peak_contact_force":0.15128,"tcp_end":[0.62567,0.15381,0.30785],"tcp_start":[0.5355,-0.02801,0.13896],"tcp_to_object_dist_end":0.03374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.62516,0.15945,0.19691],"object_pos_start":[0.63022,0.1528,0.27443],"object_to_goal_dist_end":0.0221,"object_to_goal_dist_start":0.0983,"object_z_max":0.27447,"peak_contact_force":0.13079,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2589.0,"raw_peak_contact_force":0.25201,"subtask_id":"place_object","tcp_end":[0.62873,0.16106,0.23224],"tcp_start":[0.62567,0.15381,0.30785],"tcp_to_object_dist_end":0.03555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20913,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07262,"descend_to_grasp.descend_speed":0.06846,"descend_to_place.descend_speed":0.09661,"descend_to_place.place_z_offset":0.08207,"lift.lift_height":0.19203,"lift.lift_speed":0.06092,"transport.speed":0.01351},"optimized_scores":{"best_composite_score":0.40125,"best_fitness_score":0.87125,"best_task_score":0.81715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.46027,-0.00029,-0.00117],"force_p95":0.2477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37819,"mean_force":0.05819,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45071,-0.00021,0.04916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17208.0,"contact_point_centroid":[0.45208,-0.01926,0.09495],"force_p95":0.09907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28278,"mean_force":0.05919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45125,-0.00026,0.09472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17498.0,"contact_point_centroid":[0.45283,0.0187,0.0956],"force_p95":0.09268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2704,"mean_force":0.05802,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45127,-0.00026,0.09488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":347.0,"contact_point_centroid":[0.60658,0.12803,0.2449],"force_p95":0.13632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22353,"mean_force":0.08191,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60054,0.1455,0.24974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":232.0,"contact_point_centroid":[0.60661,0.16329,0.24835],"force_p95":0.18109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2222,"mean_force":0.12556,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60023,0.14515,0.25315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7452.0,"contact_point_centroid":[0.53025,0.05359,0.19866],"force_p95":0.13145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16359,"mean_force":0.1001,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52565,0.07196,0.20156]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8474.0,"contact_point_centroid":[0.52752,0.08694,0.19698],"force_p95":0.12546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15571,"mean_force":0.08736,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52244,0.0688,0.19911]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00014,-0.00202],"force_p95":0.12936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14771,"mean_force":0.12452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45306,-0.00018,0.04868]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48422,-4e-05,0.25135]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46288,-9e-05,0.12802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.4513,-0.0194,0.0491],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09831,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.00019,0.04766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45212,0.01887,0.04887],"force_p95":0.06781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08795,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.00019,0.04766]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61782,0.14274,0.14969],"final_tcp_position":[0.60346,0.1485,0.22253],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.37819,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46756,-7e-05,0.19899],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45983,-0.00011,0.05561],"tcp_start":[0.46756,-7e-05,0.19899],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00033,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12882,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14771,"tcp_end":[0.45198,-0.00019,0.04763],"tcp_start":[0.45983,-0.00011,0.05561],"tcp_to_object_dist_end":0.02426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46311,-0.00012,0.11947],"object_pos_start":[0.46277,-0.00033,0.02591],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.23337,"object_z_max":0.1194,"peak_contact_force":0.1278,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34858.0,"raw_peak_contact_force":0.37819,"subtask_id":"lift_object","tcp_end":[0.45484,-0.0003,0.14888],"tcp_start":[0.45198,-0.00019,0.04763],"tcp_to_object_dist_end":0.03055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.60465,0.14426,0.22049],"object_pos_start":[0.46311,-0.00012,0.11947],"object_to_goal_dist_end":0.09883,"object_to_goal_dist_start":0.21222,"object_z_max":0.22038,"peak_contact_force":0.12285,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15926.0,"raw_peak_contact_force":0.16359,"tcp_end":[0.59958,0.14428,0.25779],"tcp_start":[0.45484,-0.0003,0.14888],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":72.0,"n_steps_budget":1000.0,"object_pos_end":[0.61782,0.14274,0.14969],"object_pos_start":[0.60465,0.14426,0.22049],"object_to_goal_dist_end":0.03029,"object_to_goal_dist_start":0.09883,"object_z_max":0.2205,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":579.0,"raw_peak_contact_force":0.22353,"subtask_id":"place_object","tcp_end":[0.60346,0.1485,0.22253],"tcp_start":[0.59958,0.14428,0.25779],"tcp_to_object_dist_end":0.07447,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```