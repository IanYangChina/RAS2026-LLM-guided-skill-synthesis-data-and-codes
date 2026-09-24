## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2156 | 0.85 | ❌ rejected |
| 11 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0599 | 0.86 | ❌ rejected |
| 10 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0133 | 0.86 | ❌ rejected |
| 9 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0215 | 0.86 | ✅ accepted |
| 8 | align → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2656 | 0.86 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.216) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_to_socket
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: align
- id: descend_to_entry
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.08
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: insert
- id: retract_from_hole
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
- **descend_to_entry** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.08
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.854
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.67 | 0.67 | 0.1447 |
| descend_to_entry | 0.33 | 1.00 | 0.0862 |
| insert_into_hole | 1.00 | 1.00 | 0.0013 |
| retract_from_hole | 0.33 | 0.67 | 0.0424 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.487, -0.005, 0.158) | (0.504, -0.000, 0.340)→(0.523, -0.007, 0.144) | 0.260→0.071 | 0.67 / 1.333 | 201.147 | 3335.273 |
| descend_to_entry | approach | 0.33 / step_budget | (0.487, -0.005, 0.158)→(0.506, -0.008, 0.238) | (0.523, -0.007, 0.144)→(0.531, -0.002, 0.211) | 0.071→0.135 | 1.00 / 1.667 | 335.732 | 1381.451 |
| insert_into_hole | insert | 1.00 / force_exceeded | (0.506, -0.008, 0.238)→(0.505, -0.008, 0.239) | (0.531, -0.002, 0.211)→(0.530, -0.002, 0.212) | 0.135→0.136 | 1.00 / 2.000 | 559.830 | 570.167 |
| retract_from_hole | retract | 0.33 / step_budget | (0.505, -0.008, 0.239)→(0.525, -0.005, 0.203) | (0.530, -0.002, 0.212)→(0.553, 0.002, 0.178) | 0.136→0.113 | 0.67 / 1.000 | 246.174 | 814.484 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.853
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.853
- phase_score: 0.111
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.100
- phase_breakdown.insert_score: 0.181
- phase_breakdown.align_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.408
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.859
- **Median Q (composite search score)**: 0.218
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.384


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.35455,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":-0.0122,"align_to_socket.lateral_y":0.01947,"descend_to_entry.descend_speed":0.05213,"insert_into_hole.force_threshold":30.4209,"insert_into_hole.insert_speed":0.01297,"insert_into_hole.insertion_depth":0.02626,"retract_from_hole.retract_speed":0.0934},"optimized_scores":{"best_composite_score":0.21757,"best_fitness_score":0.37757,"best_task_score":0.85932},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":894.0,"contact_point_centroid":[0.58954,0.00531,0.07986],"force_p95":328.95037,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1049.66023,"mean_force":270.36702,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.48001,0.00103,0.21107]},{"body_a":"peg_socket","body_b":"link5","contact_count":101.0,"contact_point_centroid":[0.51066,0.04269,0.07231],"force_p95":780.51711,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1042.71074,"mean_force":410.35073,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.53593,0.00248,0.2797]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47059,0.00021,0.07951],"force_p95":977.17539,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":998.81259,"mean_force":797.77635,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46276,0.00019,0.09202]},{"body_a":"peg_socket","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.58923,-0.01396,0.07966],"force_p95":945.23501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":969.82044,"mean_force":444.26149,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.49285,0.00064,0.17769]},{"body_a":"world","body_b":"link5","contact_count":635.0,"contact_point_centroid":[0.55418,0.1072,-0.00011],"force_p95":814.93961,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":969.77218,"mean_force":562.51888,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.54825,-3e-05,0.24769]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.51047,0.04288,0.07217],"force_p95":890.08864,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":897.43,"mean_force":824.01639,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53723,0.00663,0.28016]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.54048,0.01346,0.0786],"force_p95":526.96476,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":786.97553,"mean_force":123.45473,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44458,-0.00021,0.10198]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.58961,0.04294,0.07999],"force_p95":663.89457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":669.46352,"mean_force":613.774,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53723,0.00663,0.28016]},{"body_a":"peg_socket","body_b":"link6","contact_count":770.0,"contact_point_centroid":[0.58954,-0.00268,0.07987],"force_p95":287.7849,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":431.72995,"mean_force":241.32651,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46025,0.0004,0.17893]},{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56452,0.00141,0.07929],"force_p95":408.12445,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.38452,"mean_force":195.94943,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44354,-0.00021,0.11259]},{"body_a":"peg_socket","body_b":"link6","contact_count":351.0,"contact_point_centroid":[0.58957,0.04292,0.07996],"force_p95":249.47439,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.5955,"mean_force":178.63286,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.5408,0.0077,0.26371]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.5102,0.04283,0.07274],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53721,0.00731,0.28075]}],"total_contact_groups":12},"final_pose_error":0.12285,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.55973,0.00063,0.24278],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1049.66023,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.5202,0.0029,0.18204],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10406,"object_to_goal_dist_start":0.26034,"object_z_max":0.34459,"peak_contact_force":318.08591,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":828.0,"raw_peak_contact_force":998.81259,"subtask_id":"align","tcp_end":[0.48741,0.003,0.20494],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55442,0.01607,0.24518],"object_pos_start":[0.5202,0.0029,0.18204],"object_to_goal_dist_end":0.17465,"object_to_goal_dist_start":0.10406,"object_z_max":0.24524,"peak_contact_force":369.75798,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1030.0,"raw_peak_contact_force":1049.66023,"subtask_id":"approach","tcp_end":[0.53723,0.00645,0.27999],"tcp_start":[0.48741,0.003,0.20494],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55432,0.01666,0.24578],"object_pos_start":[0.55442,0.01607,0.24518],"object_to_goal_dist_end":0.17525,"object_to_goal_dist_start":0.17465,"object_z_max":0.24549,"peak_contact_force":897.43,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":897.43,"subtask_id":"insert","tcp_end":[0.53719,0.00713,0.28065],"tcp_start":[0.53723,0.00645,0.27999],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.58332,0.01298,0.21293],"object_pos_start":[0.55432,0.01666,0.24578],"object_to_goal_dist_end":0.15742,"object_to_goal_dist_start":0.17525,"object_z_max":0.24598,"peak_contact_force":425.3374,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":988.0,"raw_peak_contact_force":969.77218,"tcp_end":[0.55973,0.00063,0.24278],"tcp_start":[0.53719,0.00713,0.28065],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1619,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":-0.00613,"align_to_socket.lateral_y":0.00183,"descend_to_entry.descend_speed":0.03398,"insert_into_hole.force_threshold":24.36338,"insert_into_hole.insert_speed":0.01247,"insert_into_hole.insertion_depth":0.02718,"retract_from_hole.retract_speed":0.08737},"optimized_scores":{"best_composite_score":0.24752,"best_fitness_score":0.40752,"best_task_score":0.85267},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.57755,-0.07942,0.07704],"force_p95":1466.43734,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2017.70475,"mean_force":456.44788,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.51877,0.00058,0.15008]},{"body_a":"peg_socket","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.55493,-0.08006,0.07731],"force_p95":1453.38872,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1964.7669,"mean_force":484.27616,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.50942,0.00205,0.16022]},{"body_a":"peg_socket","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.54034,0.00761,0.07666],"force_p95":922.89074,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1188.15799,"mean_force":224.34348,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44514,-0.00272,0.10151]},{"body_a":"world","body_b":"link5","contact_count":294.0,"contact_point_centroid":[0.56741,0.09541,-0.00013],"force_p95":859.96828,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.17576,"mean_force":597.00457,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53961,-0.01956,0.24433]},{"body_a":"peg_socket","body_b":"link6","contact_count":761.0,"contact_point_centroid":[0.59591,-0.00897,0.0798],"force_p95":308.00762,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.75901,"mean_force":249.52658,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46253,-0.00734,0.16864]},{"body_a":"peg_socket","body_b":"link5","contact_count":210.0,"contact_point_centroid":[0.5234,0.03646,0.07977],"force_p95":460.39201,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":796.94618,"mean_force":393.685,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.52318,-0.02509,0.31523]},{"body_a":"peg_socket","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.59599,-0.02449,0.07885],"force_p95":492.47349,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":794.50153,"mean_force":292.77927,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.43741,-0.06751,0.24189]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50333,-0.03832,0.07989],"force_p95":626.61124,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":633.87323,"mean_force":580.8042,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.4242,-0.01164,0.19179]},{"body_a":"peg_socket","body_b":"link5","contact_count":533.0,"contact_point_centroid":[0.52309,0.03657,0.07438],"force_p95":325.61624,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.70803,"mean_force":208.19139,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52329,-0.02285,0.27761]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.53416,0.0366,0.07998],"force_p95":399.6076,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.83385,"mean_force":370.5713,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.5149,-0.03069,0.31478]},{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.56846,-0.00134,0.07802],"force_p95":313.16682,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.49403,"mean_force":57.48008,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4452,-0.00283,0.10555]},{"body_a":"peg_socket","body_b":"link6","contact_count":406.0,"contact_point_centroid":[0.59643,0.01619,0.07997],"force_p95":298.99292,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.3648,"mean_force":230.09008,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52625,-0.02124,0.26324]},{"body_a":"peg_socket","body_b":"link5","contact_count":14.0,"contact_point_centroid":[0.5064,0.03644,0.07977],"force_p95":236.90112,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.6533,"mean_force":116.9325,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.51197,-0.06507,0.29772]},{"body_a":"peg_socket","body_b":"link5","contact_count":25.0,"contact_point_centroid":[0.53246,0.03658,0.05],"force_p95":139.73891,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.82242,"mean_force":109.30754,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53351,-0.02112,0.24481]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47655,-0.00211,0.07975],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44901,-0.00206,0.08702]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54118,-0.05367,0.07829],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44447,-0.00246,0.09358]}],"total_contact_groups":16},"final_pose_error":0.12011,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.54849,-0.01622,0.2443],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":2017.70475,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.54677,-0.02235,0.14292],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08152,"object_to_goal_dist_start":0.26034,"object_z_max":0.34452,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":853.0,"raw_peak_contact_force":1188.15799,"subtask_id":"align","tcp_end":[0.50736,-0.01823,0.14833],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":960.0,"object_pos_end":[0.53576,-0.02246,0.28133],"object_pos_start":[0.54677,-0.02235,0.14292],"object_to_goal_dist_end":0.20571,"object_to_goal_dist_start":0.08152,"object_z_max":0.28542,"peak_contact_force":328.6654,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":430.0,"raw_peak_contact_force":2017.70475,"subtask_id":"approach","tcp_end":[0.51508,-0.03054,0.3146],"tcp_start":[0.50736,-0.01823,0.14833],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.53456,-0.02312,0.28303],"object_pos_start":[0.53576,-0.02246,0.28133],"object_to_goal_dist_end":0.20724,"object_to_goal_dist_start":0.20571,"object_z_max":0.28261,"peak_contact_force":402.83385,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":402.83385,"subtask_id":"insert","tcp_end":[0.51409,-0.03109,0.31646],"tcp_start":[0.51508,-0.03054,0.3146],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57324,-0.00686,0.2143],"object_pos_start":[0.53456,-0.02312,0.28303],"object_to_goal_dist_end":0.15313,"object_to_goal_dist_start":0.20724,"object_z_max":0.28371,"peak_contact_force":0.0,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1258.0,"raw_peak_contact_force":939.17576,"tcp_end":[0.54849,-0.01622,0.2443],"tcp_start":[0.51409,-0.03109,0.31646],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.43038,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.0196,"align_to_socket.lateral_y":-0.00096,"descend_to_entry.descend_speed":0.04584,"insert_into_hole.force_threshold":20.1844,"insert_into_hole.insert_speed":0.00897,"insert_into_hole.insertion_depth":0.02651,"retract_from_hole.retract_speed":0.11109},"optimized_scores":{"best_composite_score":0.18172,"best_fitness_score":0.34172,"best_task_score":0.85066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":514.0,"contact_point_centroid":[0.52964,-1e-05,0.07998],"force_p95":103.68238,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7818.84705,"mean_force":212.64206,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46373,-0.0001,0.11789]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00422,0.0651],"force_p95":335.85583,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5223.95736,"mean_force":351.34066,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46066,-8e-05,0.11396]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43902,0.0096,0.07977],"force_p95":2490.49211,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2553.25035,"mean_force":1289.15899,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43706,-0.0002,0.08377]},{"body_a":"world","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.68262,0.00056,-8e-05],"force_p95":176.33797,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1076.98889,"mean_force":92.99514,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.46542,0.00017,0.12033]},{"body_a":"world","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.68219,-0.00068,-0.00013],"force_p95":522.75332,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":534.50497,"mean_force":383.67253,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46499,0.00063,0.12023]},{"body_a":"peg_socket","body_b":"link7","contact_count":251.0,"contact_point_centroid":[0.5302,-0.00391,0.06382],"force_p95":329.53309,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.3629,"mean_force":309.30494,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.46483,0.00084,0.11935]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5302,-0.00398,0.06368],"force_p95":398.04128,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":410.23814,"mean_force":256.82201,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46498,0.0011,0.11938]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53004,-0.0043,0.06428],"force_p95":227.09649,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.76773,"mean_force":115.76289,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46508,0.0006,0.12047]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68264,-0.00048,-6e-05],"force_p95":379.22626,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.22626,"mean_force":379.22626,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.465,0.00088,0.11958]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.53026,0.0002,0.07994],"force_p95":204.55124,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.64852,"mean_force":60.16213,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46487,0.00073,0.11973]},{"body_a":"attachment","body_b":"peg_socket","contact_count":132.0,"contact_point_centroid":[0.53028,0.00051,0.07998],"force_p95":92.9582,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.29109,"mean_force":87.28067,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.46464,0.00109,0.11896]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53027,0.00044,0.07997],"force_p95":111.74184,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.26211,"mean_force":98.05936,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46492,0.00108,0.11938]},{"body_a":"world","body_b":"link6","contact_count":171.0,"contact_point_centroid":[0.68285,0.00037,-0.0],"force_p95":15.76174,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.31094,"mean_force":3.60239,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,-0.00014,0.11948]}],"total_contact_groups":13},"final_pose_error":0.00642,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46547,0.00049,0.12078],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7818.84705,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50271,-0.00016,0.10586],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02601,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":285.35398,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1510.0,"raw_peak_contact_force":7818.84705,"subtask_id":"align","tcp_end":[0.4651,-0.00022,0.11947],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.50251,0.0009,0.10575],"object_pos_start":[0.50271,-0.00016,0.10586],"object_to_goal_dist_end":0.02589,"object_to_goal_dist_start":0.02601,"object_z_max":0.10663,"peak_contact_force":308.77176,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":409.0,"raw_peak_contact_force":1076.98889,"subtask_id":"approach","tcp_end":[0.46483,0.00129,0.11917],"tcp_start":[0.4651,-0.00022,0.11947],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50252,0.00051,0.10594],"object_pos_start":[0.50251,0.0009,0.10575],"object_to_goal_dist_end":0.02606,"object_to_goal_dist_start":0.02589,"object_z_max":0.10594,"peak_contact_force":379.22626,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":410.23814,"subtask_id":"insert","tcp_end":[0.46494,0.00079,0.11964],"tcp_start":[0.46483,0.00129,0.11917],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.503,0.0002,0.10694],"object_pos_start":[0.50252,0.00051,0.10594],"object_to_goal_dist_end":0.02711,"object_to_goal_dist_start":0.02606,"object_z_max":0.10705,"peak_contact_force":313.18333,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":36.0,"raw_peak_contact_force":534.50497,"tcp_end":[0.46547,0.00049,0.12078],"tcp_start":[0.46494,0.00079,0.11964],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```