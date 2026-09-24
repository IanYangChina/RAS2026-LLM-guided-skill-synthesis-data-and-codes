## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3554 | 0.19 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0812 | 0.15 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0534 | 0.23 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2025 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1653 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.355) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_subtask
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: place_subtask
  target_entity: object
  weight: 0.8
phases:
- id: approach_obj
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
    - 0.12
    tolerance: 0.02
  parameters:
    pre_grasp_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_subtask
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
- id: grasp_phase
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_obj
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
    tolerance: 0.02
  parameters:
    lift_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_goal
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
    - 0.1
    tolerance: 0.02
  parameters:
    approach_goal_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_place
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - pre_grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_phase** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_obj** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - lift_z_offset: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_goal_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.355
- **task_score** (E): 0.188
- **fitness_score**: 0.302  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.2267 |
| descend_grasp | 1.00 | 1.00 | 0.0238 |
| grasp_phase | 1.00 | 1.00 | 0.0120 |
| lift_obj | 1.00 | 1.00 | 0.0644 |
| approach_goal | 1.00 | 1.00 | 0.3019 |
| descend_place | 1.00 | 1.00 | 0.0749 |
| release_obj | 1.00 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.013, 0.080) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / force_exceeded | (0.517, 0.013, 0.080)→(0.515, 0.005, 0.057) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 62.940 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.515, 0.005, 0.057)→(0.507, 0.005, 0.048) | (0.522, -0.001, 0.026)→(0.522, 0.003, 0.024) | 0.289→0.287 | 1.00 / 38.000 | 0.239 | 0.292 |
| lift_obj | lift | 1.00 / step_budget | (0.507, 0.005, 0.048)→(0.515, 0.004, 0.112) | (0.522, 0.003, 0.024)→(0.529, 0.001, 0.084) | 0.287→0.254 | 1.00 / 21.667 | 20.637 | 0.398 |
| approach_goal | approach | 1.00 / step_budget | (0.515, 0.004, 0.112)→(0.603, 0.199, 0.323) | (0.529, 0.001, 0.084)→(0.563, 0.053, 0.016) | 0.254→0.251 | 1.00 / 8.000 | 0.123 | 1.355 |
| descend_place | descend | 1.00 / step_budget | (0.603, 0.199, 0.323)→(0.605, 0.204, 0.248) | (0.563, 0.053, 0.016)→(0.563, 0.053, 0.016) | 0.251→0.251 | 1.00 / 8.667 | 182004.090 | 0.123 |
| release_obj | release | 1.00 / step_budget | (0.605, 0.204, 0.248)→(0.601, 0.202, 0.267) | (0.563, 0.053, 0.016)→(0.563, 0.053, 0.016) | 0.251→0.251 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.203
- phase_score: 0.358
- phase_breakdown.place_subtask_score: 0.389
- phase_breakdown.approach_subtask_score: 0.231
- grasp_place_fitness: 0.307

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.307
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.203
- **Median Q (composite search score)**: -0.354
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47368,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.11636,"approach_goal.goal_approach_speed":0.38086,"approach_obj.approach_speed":0.29886,"approach_obj.arc_height":0.09558,"approach_obj.pre_grasp_z_offset":0.05015,"descend_grasp.grasp_z_offset":0.01741,"descend_grasp.probe_force_threshold":6.98018,"descend_place.place_z_offset":0.02973,"grasp_phase.grasp_time":0.76107,"grasp_phase.retry_offset_x":0.00602,"grasp_phase.retry_offset_y":0.00525,"lift_obj.lift_z_offset":0.09754,"release_obj.release_time":0.32887},"optimized_scores":{"best_composite_score":-0.35354,"best_fitness_score":0.3036,"best_task_score":0.19134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1874.0,"contact_point_centroid":[0.53494,0.11324,-0.00247],"force_p95":0.21457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4687,"mean_force":0.14607,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5449,0.16973,0.25974]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.4818,0.05421,-0.00177],"force_p95":0.27326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38482,"mean_force":0.06365,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46869,0.05307,0.05088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2819.0,"contact_point_centroid":[0.47391,0.07124,0.07361],"force_p95":0.14363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33258,"mean_force":0.07411,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47147,0.05233,0.0744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1638.0,"contact_point_centroid":[0.49213,0.0919,0.12819],"force_p95":0.17407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30788,"mean_force":0.10893,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48723,0.07332,0.1302]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04892,-0.00236],"force_p95":0.22137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26971,"mean_force":0.14764,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47055,0.05339,0.04999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3466.0,"contact_point_centroid":[0.47309,0.03413,0.07582],"force_p95":0.11077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2635,"mean_force":0.06256,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47158,0.05232,0.07499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2335.0,"contact_point_centroid":[0.49368,0.05749,0.13281],"force_p95":0.13243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24381,"mean_force":0.08094,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48832,0.07525,0.13272]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3590.0,"contact_point_centroid":[0.47146,0.07235,0.04859],"force_p95":0.11234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15196,"mean_force":0.06076,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46945,0.05327,0.04884]},{"body_a":"world","body_b":"grasp_target","contact_count":2360.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49059,0.0802,0.21006]},{"body_a":"world","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47714,0.05781,0.06944]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.535,0.11336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57715,0.22329,0.30338]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.535,0.11336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57555,0.22428,0.27428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.4703,0.03423,0.04972],"force_p95":0.08206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08786,"mean_force":0.04383,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46947,0.05328,0.04886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1758.0,"contact_point_centroid":[0.54921,0.17596,0.27043],"force_p95":0.01172,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01555,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54869,0.17594,0.26816]},{"body_a":"left_finger","body_b":"right_finger","contact_count":521.0,"contact_point_centroid":[0.57748,0.22331,0.30573],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57715,0.22328,0.30348]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.57754,0.22517,0.27284],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00981,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57715,0.22513,0.27025]}],"total_contact_groups":16},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.535,0.11336,0.01602],"final_tcp_position":[0.57836,0.2256,0.27423],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":49.28549,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.4795,0.06223,0.08491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":49.28549,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":752.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47689,0.05411,0.05668],"tcp_start":[0.4795,0.06223,0.08491],"tcp_to_object_dist_end":0.03166,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.05182,0.02464],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28904,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.22071,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10402.0,"raw_peak_contact_force":0.26971,"tcp_end":[0.46942,0.05327,0.04882],"tcp_start":[0.47689,0.05411,0.05668],"tcp_to_object_dist_end":0.02764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.49038,0.04994,0.07651],"object_pos_start":[0.48273,0.05182,0.02464],"object_to_goal_dist_end":0.25316,"object_to_goal_dist_start":0.28904,"object_z_max":0.07625,"peak_contact_force":0.142,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6378.0,"raw_peak_contact_force":0.38482,"tcp_end":[0.4763,0.05165,0.10352],"tcp_start":[0.46942,0.05327,0.04882],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.535,0.11336,0.01602],"object_pos_start":[0.49038,0.04994,0.07651],"object_to_goal_dist_end":0.24805,"object_to_goal_dist_start":0.25316,"object_z_max":0.12906,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7605.0,"raw_peak_contact_force":1.4687,"tcp_end":[0.57635,0.22127,0.32938],"tcp_start":[0.4763,0.05165,0.10352],"tcp_to_object_dist_end":0.33399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.535,0.11336,0.01602],"object_pos_start":[0.535,0.11336,0.01602],"object_to_goal_dist_end":0.24805,"object_to_goal_dist_start":0.24805,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1009.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_subtask","tcp_end":[0.57836,0.2256,0.27423],"tcp_start":[0.57635,0.22127,0.32938],"tcp_to_object_dist_end":0.28486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.535,0.11336,0.01602],"object_pos_start":[0.535,0.11336,0.01602],"object_to_goal_dist_end":0.24805,"object_to_goal_dist_start":0.24805,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5747,0.22378,0.29401],"tcp_start":[0.57836,0.2256,0.27423],"tcp_to_object_dist_end":0.30174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37963,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.14447,"approach_goal.goal_approach_speed":0.22791,"approach_obj.approach_speed":0.26159,"approach_obj.arc_height":0.11539,"approach_obj.pre_grasp_z_offset":0.05016,"descend_grasp.grasp_z_offset":0.02341,"descend_grasp.probe_force_threshold":8.22166,"descend_place.place_z_offset":0.02589,"grasp_phase.grasp_time":0.84808,"grasp_phase.retry_offset_x":0.00037,"grasp_phase.retry_offset_y":0.00081,"lift_obj.lift_z_offset":0.11594,"release_obj.release_time":0.36328},"optimized_scores":{"best_composite_score":-0.36265,"best_fitness_score":0.2945,"best_task_score":0.17134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2680.0,"contact_point_centroid":[0.57069,0.04905,-0.00229],"force_p95":0.13618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39654,"mean_force":0.14148,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57813,0.13534,0.25789]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.53576,-0.01446,-0.00187],"force_p95":0.32334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42082,"mean_force":0.06269,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52094,-0.01492,0.04871]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02101,-0.00247],"force_p95":0.25409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30522,"mean_force":0.15556,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52312,-0.01488,0.04783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3717.0,"contact_point_centroid":[0.5276,0.00316,0.07856],"force_p95":0.14406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30113,"mean_force":0.07973,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52427,-0.01573,0.07878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3985.0,"contact_point_centroid":[0.52734,-0.03419,0.08064],"force_p95":0.129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29284,"mean_force":0.07442,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52434,-0.01574,0.07934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1353.0,"contact_point_centroid":[0.54107,0.02185,0.13544],"force_p95":0.17674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28122,"mean_force":0.11156,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53513,0.00358,0.13666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1915.0,"contact_point_centroid":[0.54156,-0.01246,0.13866],"force_p95":0.13347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21327,"mean_force":0.08123,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53559,0.00528,0.13807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4043.0,"contact_point_centroid":[0.52343,0.00435,0.04718],"force_p95":0.0993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14761,"mean_force":0.05545,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52192,-0.01486,0.04642]},{"body_a":"world","body_b":"grasp_target","contact_count":2624.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.12998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51556,0.05695,0.18422]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53007,-0.01258,0.06214]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.5706,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60652,0.22125,0.29266]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5706,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60412,0.22324,0.24649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4893.0,"contact_point_centroid":[0.52304,-0.03442,0.04747],"force_p95":0.09287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10048,"mean_force":0.04687,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52194,-0.01486,0.04645]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2661.0,"contact_point_centroid":[0.58068,0.14161,0.26607],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58025,0.14161,0.26376]},{"body_a":"left_finger","body_b":"right_finger","contact_count":769.0,"contact_point_centroid":[0.60706,0.22126,0.29486],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60652,0.22126,0.29267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60663,0.22418,0.24506],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60595,0.22416,0.24293]}],"total_contact_groups":16},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5706,0.04939,0.01602],"final_tcp_position":[0.60733,0.22464,0.24726],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.20082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53223,-0.00776,0.07605],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":70.16624,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52993,-0.01497,0.05586],"tcp_start":[0.53223,-0.00776,0.07605],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53718,-0.01721,0.02426],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31448,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.25214,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10736.0,"raw_peak_contact_force":0.30522,"tcp_end":[0.52189,-0.01486,0.04638],"tcp_start":[0.52993,-0.01497,0.05586],"tcp_to_object_dist_end":0.02699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":264.0,"n_steps_budget":630.0,"object_pos_end":[0.54502,-0.01928,0.09398],"object_pos_start":[0.53718,-0.01721,0.02426],"object_to_goal_dist_end":0.27957,"object_to_goal_dist_start":0.31448,"object_z_max":0.09374,"peak_contact_force":0.14568,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7804.0,"raw_peak_contact_force":0.42082,"tcp_end":[0.53092,-0.01682,0.12125],"tcp_start":[0.52189,-0.01486,0.04638],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.5706,0.04939,0.01602],"object_pos_start":[0.54502,-0.01928,0.09398],"object_to_goal_dist_end":0.26462,"object_to_goal_dist_start":0.27957,"object_z_max":0.1245,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8609.0,"raw_peak_contact_force":1.39654,"tcp_end":[0.60615,0.21828,0.33501],"tcp_start":[0.53092,-0.01682,0.12125],"tcp_to_object_dist_end":0.36269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.5706,0.04939,0.01602],"object_pos_start":[0.5706,0.04939,0.01602],"object_to_goal_dist_end":0.26462,"object_to_goal_dist_start":0.26462,"object_z_max":0.01602,"peak_contact_force":273006.20082,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1493.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_subtask","tcp_end":[0.60733,0.22464,0.24726],"tcp_start":[0.60615,0.21828,0.33501],"tcp_to_object_dist_end":0.29246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5706,0.04939,0.01602],"object_pos_start":[0.5706,0.04939,0.01602],"object_to_goal_dist_end":0.26462,"object_to_goal_dist_start":0.26462,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6031,0.2227,0.26589],"tcp_start":[0.60733,0.22464,0.24726],"tcp_to_object_dist_end":0.30582,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30208,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.14543,"approach_goal.goal_approach_speed":0.29435,"approach_obj.approach_speed":0.38546,"approach_obj.arc_height":0.10508,"approach_obj.pre_grasp_z_offset":0.05236,"descend_grasp.grasp_z_offset":0.02739,"descend_grasp.probe_force_threshold":7.3032,"descend_place.place_z_offset":0.03313,"grasp_phase.grasp_time":0.7512,"grasp_phase.retry_offset_x":-0.00011,"grasp_phase.retry_offset_y":-0.00276,"lift_obj.lift_z_offset":0.10544,"release_obj.release_time":0.46695},"optimized_scores":{"best_composite_score":-0.35015,"best_fitness_score":0.30699,"best_task_score":0.20278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2478.0,"contact_point_centroid":[0.58309,-0.00515,-0.00226],"force_p95":0.1301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1993,"mean_force":0.13721,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59144,0.08622,0.22747]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.5456,-0.02201,-0.00186],"force_p95":0.26458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38944,"mean_force":0.05811,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52948,-0.0227,0.05136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.53702,-0.00464,0.07339],"force_p95":0.15071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33307,"mean_force":0.10754,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53286,-0.02338,0.07613]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54585,-0.02886,-0.00245],"force_p95":0.25489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30183,"mean_force":0.15417,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53153,-0.02269,0.05059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3416.0,"contact_point_centroid":[0.53595,-0.0414,0.07637],"force_p95":0.13158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28171,"mean_force":0.07649,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53276,-0.02337,0.07575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":495.0,"contact_point_centroid":[0.54794,0.00315,0.11646],"force_p95":0.20024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23792,"mean_force":0.13508,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54211,-0.01532,0.1188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.54815,-0.03192,0.11977],"force_p95":0.14006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22799,"mean_force":0.08061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5425,-0.01428,0.11974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2806.0,"contact_point_centroid":[0.53249,-0.0038,0.04682],"force_p95":0.12971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14347,"mean_force":0.07715,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53031,-0.02265,0.04913]},{"body_a":"world","body_b":"grasp_target","contact_count":2588.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.52045,0.05031,0.18236]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53854,-0.02063,0.06478]},{"body_a":"world","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.58321,-0.00517,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62783,0.1593,0.26603]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58321,-0.00517,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62512,0.16101,0.22293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5071.0,"contact_point_centroid":[0.53169,-0.04171,0.04972],"force_p95":0.08928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09826,"mean_force":0.04415,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53034,-0.02265,0.04916]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2314.0,"contact_point_centroid":[0.59633,0.09501,0.23948],"force_p95":0.01132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59589,0.09501,0.23717]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62762,0.16177,0.22178],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62728,0.16175,0.21944]},{"body_a":"left_finger","body_b":"right_finger","contact_count":718.0,"contact_point_centroid":[0.62821,0.15931,0.26809],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62783,0.15931,0.2659]}],"total_contact_groups":16},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.58321,-0.00517,0.01602],"final_tcp_position":[0.62888,0.16214,0.22382],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273005.94645,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2588.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.54068,-0.01594,0.07803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":69.36807,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53839,-0.02286,0.0589],"tcp_start":[0.54068,-0.01594,0.07803],"tcp_to_object_dist_end":0.03426,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54598,-0.02478,0.02441],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25845,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.2437,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9677.0,"raw_peak_contact_force":0.30183,"tcp_end":[0.53029,-0.02265,0.0491],"tcp_start":[0.53839,-0.02286,0.0589],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.55211,-0.02712,0.08164],"object_pos_start":[0.54598,-0.02478,0.02441],"object_to_goal_dist_end":0.22909,"object_to_goal_dist_start":0.25845,"object_z_max":0.08141,"peak_contact_force":61.62372,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5618.0,"raw_peak_contact_force":0.38944,"tcp_end":[0.53924,-0.02433,0.11114],"tcp_start":[0.53029,-0.02265,0.0491],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.58321,-0.00517,0.01602],"object_pos_start":[0.55211,-0.02712,0.08164],"object_to_goal_dist_end":0.23935,"object_to_goal_dist_start":0.22909,"object_z_max":0.09641,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6243.0,"raw_peak_contact_force":1.1993,"tcp_end":[0.62732,0.1568,0.30512],"tcp_start":[0.53924,-0.02433,0.11114],"tcp_to_object_dist_end":0.33431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":168.0,"n_steps_budget":1000.0,"object_pos_end":[0.58321,-0.00517,0.01602],"object_pos_start":[0.58321,-0.00517,0.01602],"object_to_goal_dist_end":0.23935,"object_to_goal_dist_start":0.23935,"object_z_max":0.01602,"peak_contact_force":273005.94645,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1390.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_subtask","tcp_end":[0.62888,0.16214,0.22382],"tcp_start":[0.62732,0.1568,0.30512],"tcp_to_object_dist_end":0.27067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58321,-0.00517,0.01602],"object_pos_start":[0.58321,-0.00517,0.01602],"object_to_goal_dist_end":0.23935,"object_to_goal_dist_start":0.23935,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6239,0.16056,0.24229],"tcp_start":[0.62888,0.16214,0.22382],"tcp_to_object_dist_end":0.28341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```