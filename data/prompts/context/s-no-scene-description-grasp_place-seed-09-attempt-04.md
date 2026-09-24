## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1455 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0380 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1077 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0077 | 0.17 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.146) — your mutation base

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
    - 0.02
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
    anchor: current_tcp
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
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: place_object
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=grasp_lift_check, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.146
- **task_score** (E): 0.166
- **fitness_score**: 0.284  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1098 |
| descend_to_grasp | 1.00 | 1.00 | 0.1322 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift | 1.00 | 1.00 | 0.0779 |
| transport | 0.67 | 1.00 | 0.2533 |
| descend_to_place | 1.00 | 1.00 | 0.1059 |
| release | 1.00 | 1.00 | 0.0209 |
| retract | 1.00 | 1.00 | 0.0850 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.065) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.065)→(0.502, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 26.333 | 0.141 | 0.181 |
| lift | lift | 1.00 / step_budget | (0.502, -0.016, 0.055)→(0.494, -0.016, 0.132) | (0.515, -0.017, 0.026)→(0.505, -0.009, 0.019) | 0.270→0.273 | 1.00 / 7.333 | 0.142 | 0.934 |
| transport | approach | 0.67 / step_budget | (0.494, -0.016, 0.132)→(0.601, 0.155, 0.277) | (0.505, -0.009, 0.019)→(0.505, -0.009, 0.019) | 0.273→0.273 | 1.00 / 8.333 | 0.123 | 0.142 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.155, 0.277)→(0.607, 0.173, 0.175) | (0.505, -0.009, 0.019)→(0.505, -0.009, 0.019) | 0.273→0.273 | 1.00 / 8.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.607, 0.173, 0.175)→(0.602, 0.172, 0.195) | (0.505, -0.009, 0.019)→(0.505, -0.009, 0.019) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.602, 0.172, 0.195)→(0.599, 0.171, 0.280) | (0.505, -0.009, 0.019)→(0.505, -0.009, 0.019) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.215
- phase_score: 0.525
- phase_breakdown.lift_object_score: 0.185
- phase_breakdown.reach_object_score: 0.274
- phase_breakdown.place_object_score: 0.737
- grasp_place_fitness: 0.308

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.308
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.215
- **Median Q (composite search score)**: -0.149
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.407


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10638,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.10727,"descend_to_grasp.descend_speed":0.13529,"descend_to_place.descend_speed":0.02076,"lift.lift_height":0.05086,"transport.speed":0.0471},"optimized_scores":{"best_composite_score":-0.16579,"best_fitness_score":0.26421,"best_task_score":0.12459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":459.0,"contact_point_centroid":[0.51814,-0.01698,-0.00263],"force_p95":0.60893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72539,"mean_force":0.18229,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51688,-0.02029,0.07477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7959.0,"contact_point_centroid":[0.51782,-0.00165,0.0767],"force_p95":0.12992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40424,"mean_force":0.09004,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51718,-0.02029,0.0803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9148.0,"contact_point_centroid":[0.51767,-0.0387,0.07687],"force_p95":0.10665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27555,"mean_force":0.07703,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51706,-0.02029,0.08064]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02126,-0.00207],"force_p95":0.14406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18759,"mean_force":0.12784,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52397,-0.02043,0.0559]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.51177,0.00135,-0.002],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18163,"mean_force":0.12254,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55815,0.10244,0.21408]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5126,-0.00822,0.2495]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52839,-0.01885,0.13131]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.51177,0.00135,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59558,0.2037,0.22039]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51177,0.00135,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59418,0.20958,0.20756]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.51177,0.00135,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59057,0.20804,0.26727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.52377,-0.00166,0.05154],"force_p95":0.09819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10645,"mean_force":0.07623,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52281,-0.02041,0.05453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2969.0,"contact_point_centroid":[0.52343,-0.03911,0.05138],"force_p95":0.09353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09361,"mean_force":0.0697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52281,-0.02041,0.05453]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5907.0,"contact_point_centroid":[0.55907,0.10387,0.21779],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55868,0.10387,0.21553]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.59713,0.21058,0.20633],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01028,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5965,0.21054,0.20407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2517.0,"contact_point_centroid":[0.59611,0.20368,0.22266],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01034,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59556,0.20365,0.22044]}],"total_contact_groups":15},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.51177,0.00135,0.01602],"final_tcp_position":[0.59095,0.20812,0.31216],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.72539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52723,-0.0172,0.19689],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":964.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53141,-0.02055,0.0651],"tcp_start":[0.52723,-0.0172,0.19689],"tcp_to_object_dist_end":0.03948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.0207,0.02576],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14167,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7433.0,"raw_peak_contact_force":0.18759,"tcp_end":[0.52278,-0.02041,0.05449],"tcp_start":[0.53141,-0.02055,0.0651],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.51198,0.00292,0.01447],"object_pos_start":[0.53697,-0.0207,0.02576],"object_to_goal_dist_end":0.31216,"object_to_goal_dist_start":0.3164,"object_z_max":0.06074,"peak_contact_force":0.18163,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17566.0,"raw_peak_contact_force":0.72539,"subtask_id":"lift_object","tcp_end":[0.51372,-0.02022,0.08976],"tcp_start":[0.52278,-0.02041,0.05449],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51177,0.00135,0.01602],"object_pos_start":[0.51198,0.00292,0.01447],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31216,"object_z_max":0.01609,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11507.0,"raw_peak_contact_force":0.18163,"tcp_end":[0.58233,0.16709,0.27773],"tcp_start":[0.51372,-0.02022,0.08976],"tcp_to_object_dist_end":0.31772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.51177,0.00135,0.01602],"object_pos_start":[0.51177,0.00135,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4849.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59769,0.21099,0.20706],"tcp_start":[0.58233,0.16709,0.27773],"tcp_to_object_dist_end":0.29636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51177,0.00135,0.01602],"object_pos_start":[0.51177,0.00135,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59287,0.20901,0.227],"tcp_start":[0.59769,0.21099,0.20706],"tcp_to_object_dist_end":0.30694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.51177,0.00135,0.01602],"object_pos_start":[0.51177,0.00135,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59095,0.20812,0.31216],"tcp_start":[0.59287,0.20901,0.227],"tcp_to_object_dist_end":0.36976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90206,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.12931,"descend_to_grasp.descend_speed":0.07391,"descend_to_place.descend_speed":0.12064,"lift.lift_height":0.18867,"transport.speed":0.10469},"optimized_scores":{"best_composite_score":-0.14858,"best_fitness_score":0.28142,"best_task_score":0.15815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2526.0,"contact_point_centroid":[0.55048,-0.04356,-0.00232],"force_p95":0.14705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49274,"mean_force":0.13741,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52557,-0.02779,0.1981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6647.0,"contact_point_centroid":[0.5312,-0.00953,0.10464],"force_p95":0.13673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35443,"mean_force":0.10181,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52681,-0.02783,0.10817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7111.0,"contact_point_centroid":[0.5307,-0.04601,0.1054],"force_p95":0.13537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27905,"mean_force":0.09556,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52681,-0.02783,0.10905]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02914,-0.0021],"force_p95":0.15216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20553,"mean_force":0.13009,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53213,-0.02801,0.05517]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51621,-0.01147,0.24852]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53609,-0.02601,0.13039]},{"body_a":"world","body_b":"grasp_target","contact_count":4560.0,"contact_point_centroid":[0.55101,-0.04469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59136,0.09608,0.27538]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.55101,-0.04469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62487,0.15939,0.20757]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55101,-0.04469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62045,0.15925,0.18689]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55101,-0.04469,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61637,0.15796,0.24613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2543.0,"contact_point_centroid":[0.53242,-0.00925,0.05097],"force_p95":0.11205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12105,"mean_force":0.08203,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53095,-0.02797,0.05375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.53171,-0.04661,0.05072],"force_p95":0.09468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09555,"mean_force":0.06902,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53095,-0.02797,0.05376]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2305.0,"contact_point_centroid":[0.52547,-0.02778,0.21155],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52513,-0.02777,0.20915]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4865.0,"contact_point_centroid":[0.59166,0.09587,0.27754],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01045,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59124,0.09586,0.27525]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2480.0,"contact_point_centroid":[0.62535,0.15941,0.20983],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62486,0.15938,0.20766]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62373,0.16008,0.1859],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01027,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62305,0.16004,0.18361]}],"total_contact_groups":16},"final_pose_error":0.01561,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55101,-0.04469,0.01602],"final_tcp_position":[0.61671,0.158,0.29075],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.49274,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53461,-0.02392,0.19535],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":996.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53964,-0.02821,0.06462],"tcp_start":[0.53461,-0.02392,0.19535],"tcp_to_object_dist_end":0.03908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54566,-0.02827,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7335.0,"raw_peak_contact_force":0.20553,"tcp_end":[0.53092,-0.02797,0.05371],"tcp_start":[0.53964,-0.02821,0.06462],"tcp_to_object_dist_end":0.03172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55101,-0.04469,0.01602],"object_pos_start":[0.54566,-0.02827,0.02563],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.26042,"object_z_max":0.13138,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18589.0,"raw_peak_contact_force":1.49274,"subtask_id":"lift_object","tcp_end":[0.5239,-0.02773,0.20972],"tcp_start":[0.53092,-0.02797,0.05371],"tcp_to_object_dist_end":0.19632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.55101,-0.04469,0.01602],"object_pos_start":[0.55101,-0.04469,0.01602],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.27664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9425.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62312,0.15315,0.3035],"tcp_start":[0.5239,-0.02773,0.20972],"tcp_to_object_dist_end":0.35635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.55101,-0.04469,0.01602],"object_pos_start":[0.55101,-0.04469,0.01602],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.27664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4816.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62436,0.16042,0.1867],"tcp_start":[0.62312,0.15315,0.3035],"tcp_to_object_dist_end":0.27673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55101,-0.04469,0.01602],"object_pos_start":[0.55101,-0.04469,0.01602],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.27664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61895,0.15876,0.20618],"tcp_start":[0.62436,0.16042,0.1867],"tcp_to_object_dist_end":0.28666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55101,-0.04469,0.01602],"object_pos_start":[0.55101,-0.04469,0.01602],"object_to_goal_dist_end":0.27664,"object_to_goal_dist_start":0.27664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61671,0.158,0.29075],"tcp_start":[0.61895,0.15876,0.20618],"tcp_to_object_dist_end":0.34768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28862,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.15228,"descend_to_grasp.descend_speed":0.12549,"descend_to_place.descend_speed":0.06777,"lift.lift_height":0.05364,"transport.speed":0.02729},"optimized_scores":{"best_composite_score":-0.12227,"best_fitness_score":0.30773,"best_task_score":0.21454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2654.0,"contact_point_centroid":[0.45187,0.01338,-0.00206],"force_p95":0.23213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58335,"mean_force":0.1289,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44623,-0.00023,0.09315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1494.0,"contact_point_centroid":[0.44803,-0.01889,0.06167],"force_p95":0.15238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29769,"mean_force":0.1024,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44935,-0.00021,0.0652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2005.0,"contact_point_centroid":[0.44902,0.01794,0.06158],"force_p95":0.11782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2722,"mean_force":0.07916,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4493,-0.00021,0.06557]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46286,-0.00018,-0.00202],"force_p95":0.13112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14838,"mean_force":0.12454,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45339,-0.00017,0.0584]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.46286,-7e-05,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48424,-4e-05,0.25101]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46313,-8e-05,0.13259]},{"body_a":"world","body_b":"grasp_target","contact_count":5492.0,"contact_point_centroid":[0.45144,0.01549,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54485,0.09536,0.19886]},{"body_a":"world","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.45144,0.01549,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59992,0.14841,0.15404]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45144,0.01549,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59491,0.14771,0.13346]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.45144,0.01549,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58984,0.14629,0.19378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2193.0,"contact_point_centroid":[0.45042,-0.01896,0.05437],"force_p95":0.11407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11489,"mean_force":0.0903,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45235,-0.00018,0.05738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.45195,0.01823,0.0535],"force_p95":0.09135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09201,"mean_force":0.06948,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45236,-0.00018,0.05738]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2204.0,"contact_point_centroid":[0.44584,-0.00023,0.09972],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01079,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44553,-0.00023,0.09752]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2550.0,"contact_point_centroid":[0.60051,0.14842,0.15659],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59991,0.14839,0.15439]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5833.0,"contact_point_centroid":[0.54566,0.09577,0.20151],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54529,0.09576,0.1993]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.59827,0.1486,0.13171],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59801,0.14857,0.12962]}],"total_contact_groups":16},"final_pose_error":0.01504,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.45144,0.01549,0.02602],"final_tcp_position":[0.59006,0.14631,0.23845],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.58335,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46772,-7e-05,0.19894],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46007,-0.0001,0.06536],"tcp_start":[0.46772,-7e-05,0.19894],"tcp_to_object_dist_end":0.03944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00055,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23351,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13023,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6921.0,"raw_peak_contact_force":0.14838,"tcp_end":[0.45233,-0.00018,0.05735],"tcp_start":[0.46007,-0.0001,0.06536],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.45144,0.01549,0.02602],"object_pos_start":[0.46277,-0.00055,0.02592],"object_to_goal_dist_end":0.23089,"object_to_goal_dist_start":0.23351,"object_z_max":0.0388,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8357.0,"raw_peak_contact_force":0.58335,"subtask_id":"lift_object","tcp_end":[0.44413,-0.00024,0.09762],"tcp_start":[0.45233,-0.00018,0.05735],"tcp_to_object_dist_end":0.07367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.45144,0.01549,0.02602],"object_pos_start":[0.45144,0.01549,0.02602],"object_to_goal_dist_end":0.23089,"object_to_goal_dist_start":0.23089,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11325.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59739,0.14468,0.24837],"tcp_start":[0.44413,-0.00024,0.09762],"tcp_to_object_dist_end":0.29569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.45144,0.01549,0.02602],"object_pos_start":[0.45144,0.01549,0.02602],"object_to_goal_dist_end":0.23089,"object_to_goal_dist_start":0.23089,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4946.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59953,0.14897,0.13242],"tcp_start":[0.59739,0.14468,0.24837],"tcp_to_object_dist_end":0.22598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45144,0.01549,0.02602],"object_pos_start":[0.45144,0.01549,0.02602],"object_to_goal_dist_end":0.23089,"object_to_goal_dist_start":0.23089,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59308,0.14719,0.15316],"tcp_start":[0.59953,0.14897,0.13242],"tcp_to_object_dist_end":0.23145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.45144,0.01549,0.02602],"object_pos_start":[0.45144,0.01549,0.02602],"object_to_goal_dist_end":0.23089,"object_to_goal_dist_start":0.23089,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59006,0.14631,0.23845],"tcp_start":[0.59308,0.14719,0.15316],"tcp_to_object_dist_end":0.28541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```