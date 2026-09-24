## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0107 | 0.35 | ❌ rejected |
| 7 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0635 | 0.00 | ❌ rejected |
| 6 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4735 | 0.82 | ❌ rejected |
| 5 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2073 | 0.01 | ❌ rejected |
| 4 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.1645 | 0.08 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.011) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.08
    orientation:
      mode: none
  parameters:
    clearance_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_final
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.08]
  - orientation: mode=none
  - parameter_bindings:
    - clearance_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_final** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.011
- **task_score** (E): 0.349
- **fitness_score**: 0.249  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.67 | 1.00 | 0.1942 |
| approach_final | 0.33 | 1.00 | 0.0894 |
| contact_peg | 1.00 | 1.00 | 0.0011 |
| push_through | 0.00 | 1.00 | 0.0580 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.042, 0.191) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.551 | 2.179 |
| approach_final | approach | 0.33 / step_budget | (0.495, 0.042, 0.191)→(0.498, 0.058, 0.104) | (0.500, 0.081, 0.034)→(0.505, 0.076, 0.031) | 0.161→0.157 | 1.00 / 3.333 | 294.640 | 391.492 |
| contact_peg | contact | 1.00 / force_exceeded | (0.498, 0.058, 0.104)→(0.497, 0.058, 0.104) | (0.505, 0.076, 0.031)→(0.506, 0.076, 0.031) | 0.157→0.157 | 1.00 / 3.000 | 81.913 | 158.990 |
| push_through | push | 0.00 / step_budget | (0.497, 0.058, 0.104)→(0.504, 0.004, 0.083) | (0.506, 0.076, 0.031)→(0.499, 0.013, 0.024) | 0.157→0.095 | 1.00 / 3.000 | 488.131 | 571.637 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.466
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.455
- phase_score: 0.194
- phase_breakdown.push_score: 0.232
- phase_breakdown.contact_score: 0.147
- phase_breakdown.approach_score: 0.124

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.298
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.455
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26728,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.08188,"approach_high.arc_height":0.28216,"approach_high.clearance_height":0.17691,"approach_high.speed":0.04527,"contact_peg.contact_force":9.01832,"contact_peg.speed":0.02993,"push_through.push_distance":0.23466,"push_through.push_speed":0.02671,"push_through.push_tolerance":0.02146},"optimized_scores":{"best_composite_score":0.03825,"best_fitness_score":0.29825,"best_task_score":0.45517},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":780.0,"contact_point_centroid":[0.52507,0.02344,0.05992],"force_p95":419.78407,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.88375,"mean_force":376.93454,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50113,-0.03125,0.09595]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":416.0,"contact_point_centroid":[0.52508,0.11814,0.0599],"force_p95":432.42062,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.41904,"mean_force":360.77719,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49877,0.03346,0.1123]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":751.0,"contact_point_centroid":[0.47499,0.0593,0.05999],"force_p95":154.97831,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.58913,"mean_force":108.69004,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50086,-0.0304,0.09627]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52503,0.11918,0.05996],"force_p95":238.88437,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.41709,"mean_force":171.08984,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49456,0.04351,0.12533]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.525,0.11999,0.05973],"force_p95":244.1972,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.1972,"mean_force":244.1972,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49466,0.04346,0.12533]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":173.0,"contact_point_centroid":[0.525,0.11998,0.05979],"force_p95":180.20262,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.49495,"mean_force":140.48139,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49619,0.03878,0.12012]},{"body_a":"peg","body_b":"link7","contact_count":162.0,"contact_point_centroid":[0.50401,0.04495,0.06393],"force_p95":104.92841,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.05715,"mean_force":74.62288,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49544,-0.00208,0.10538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50134,-0.00347,0.00831],"force_p95":82.33698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.7086,"mean_force":11.83847,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4998,-0.02375,0.09855]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":67.00108,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.09963,"mean_force":26.78475,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50136,-0.0301,0.09595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":822.0,"contact_point_centroid":[0.50344,0.05705,0.00934],"force_p95":19.20564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.35267,"mean_force":3.06525,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50193,0.02947,0.13629]},{"body_a":"peg","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.50307,0.07466,0.05813],"force_p95":57.2306,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.88488,"mean_force":23.06782,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50341,0.02505,0.10229]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52505,0.01909,0.05922],"force_p95":36.73934,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.47949,"mean_force":27.57674,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49657,-0.01146,0.10155]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47498,0.11999,0.05997],"force_p95":15.18546,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15.18546,"mean_force":15.18546,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49217,0.04239,0.12514]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.0616,0.00936],"force_p95":0.58193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55487,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50111,0.12353,0.277]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50412,0.20779,0.29837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49707,0.05618,0.00938],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55101,"mean_force":0.54665,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49351,0.04314,0.12528]}],"total_contact_groups":17},"final_pose_error":0.15911,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5055,-0.01294,0.02419],"final_tcp_position":[0.49999,-0.03354,0.09626],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":487.88375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50869,0.02806,0.22403],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50414,0.05476,0.0338],"object_pos_start":[0.50377,0.06159,0.03378],"object_to_goal_dist_end":0.13497,"object_to_goal_dist_start":0.14178,"object_z_max":0.03498,"peak_contact_force":288.82741,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1501.0,"raw_peak_contact_force":456.41904,"subtask_id":"approach","tcp_end":[0.49466,0.04346,0.12533],"tcp_start":[0.50869,0.02806,0.22403],"tcp_to_object_dist_end":0.09271,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50418,0.05484,0.03381],"object_pos_start":[0.50414,0.05476,0.0338],"object_to_goal_dist_end":0.13505,"object_to_goal_dist_start":0.13497,"object_z_max":0.03381,"peak_contact_force":15.18546,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":246.41709,"subtask_id":"contact","tcp_end":[0.49182,0.04206,0.12506],"tcp_start":[0.49466,0.04346,0.12533],"tcp_to_object_dist_end":0.09297,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5055,-0.01294,0.02419],"object_pos_start":[0.50418,0.05484,0.03381],"object_to_goal_dist_end":0.06912,"object_to_goal_dist_start":0.13505,"object_z_max":0.03988,"peak_contact_force":397.48113,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2866.0,"raw_peak_contact_force":487.88375,"subtask_id":"push","tcp_end":[0.49999,-0.03354,0.09626],"tcp_start":[0.49182,0.04206,0.12506],"tcp_to_object_dist_end":0.07516,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28324,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.03557,"approach_high.arc_height":0.16459,"approach_high.clearance_height":0.14327,"approach_high.speed":0.07738,"contact_peg.contact_force":14.86793,"contact_peg.speed":0.03364,"push_through.push_distance":0.23359,"push_through.push_speed":0.04659,"push_through.push_tolerance":0.02716},"optimized_scores":{"best_composite_score":-0.057,"best_fitness_score":0.203,"best_task_score":0.25827},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":194.0,"contact_point_centroid":[0.47481,0.11969,0.05976],"force_p95":657.63306,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":718.86832,"mean_force":559.64396,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51322,0.07939,0.05798]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":185.0,"contact_point_centroid":[0.52513,0.08156,0.05808],"force_p95":509.48601,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":559.50226,"mean_force":369.57184,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51342,0.08044,0.05847]},{"body_a":"peg","body_b":"link7","contact_count":814.0,"contact_point_centroid":[0.50538,0.14411,0.03533],"force_p95":265.70426,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":319.149,"mean_force":215.65665,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51214,0.09586,0.06584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50429,0.10802,0.00714],"force_p95":261.61067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":306.81238,"mean_force":178.1138,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51235,0.093,0.06442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5007,0.11706,0.00805],"force_p95":216.0864,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":266.04213,"mean_force":112.33121,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50149,0.08604,0.10101]},{"body_a":"peg","body_b":"link7","contact_count":723.0,"contact_point_centroid":[0.49967,0.14497,0.0395],"force_p95":228.27323,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":240.45876,"mean_force":166.92923,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50302,0.09048,0.08106]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52504,0.11959,0.05999],"force_p95":161.68805,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.37739,"mean_force":69.90306,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51237,0.07758,0.05861]},{"body_a":"attachment","body_b":"peg","contact_count":806.0,"contact_point_centroid":[0.50729,0.13354,0.05604],"force_p95":101.15357,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.06127,"mean_force":72.56409,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51214,0.09602,0.06589]},{"body_a":"peg","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50178,0.14437,0.03724],"force_p95":119.55936,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.55936,"mean_force":119.55936,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50677,0.10007,0.06405]},{"body_a":"peg","body_b":"world","contact_count":611.0,"contact_point_centroid":[0.50567,0.11962,-0.00035],"force_p95":89.57276,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.17596,"mean_force":37.25729,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50358,0.09241,0.07757]},{"body_a":"attachment","body_b":"peg","contact_count":179.0,"contact_point_centroid":[0.50522,0.13515,0.05667],"force_p95":104.98428,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.48301,"mean_force":61.8984,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50528,0.09796,0.06701]},{"body_a":"peg","body_b":"world","contact_count":781.0,"contact_point_centroid":[0.50371,0.11672,-0.00096],"force_p95":91.29218,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.74523,"mean_force":70.9404,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51209,0.09631,0.06596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49216,0.11609,0.00702],"force_p95":81.03457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.03457,"mean_force":81.03457,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50677,0.10007,0.06405]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":169.0,"contact_point_centroid":[0.52531,0.10781,0.01834],"force_p95":42.95489,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.86042,"mean_force":18.60196,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51012,0.09702,0.06531]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50756,0.11763,-0.00153],"force_p95":51.37883,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.37883,"mean_force":51.37883,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50677,0.10007,0.06405]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":144.0,"contact_point_centroid":[0.52522,0.11153,0.01602],"force_p95":28.46859,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.6066,"mean_force":12.51081,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.5056,0.09853,0.06647]}],"total_contact_groups":20},"final_pose_error":0.18962,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49651,0.07471,0.0247],"final_tcp_position":[0.51327,0.08,0.05768],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":718.86832,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.11609,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55222,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":719.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49898,0.07514,0.19292],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,0.12661,0.02642],"object_pos_start":[0.501,0.11609,0.03386],"object_to_goal_dist_end":0.20719,"object_to_goal_dist_start":0.19619,"object_z_max":0.03394,"peak_contact_force":223.81113,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2657.0,"raw_peak_contact_force":266.04213,"subtask_id":"approach","tcp_end":[0.50677,0.10007,0.06405],"tcp_start":[0.49898,0.07514,0.19292],"tcp_to_object_dist_end":0.04606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50763,0.12665,0.0264],"object_pos_start":[0.50754,0.12661,0.02642],"object_to_goal_dist_end":0.20724,"object_to_goal_dist_start":0.20719,"object_z_max":0.02642,"peak_contact_force":119.55936,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":119.55936,"subtask_id":"contact","tcp_end":[0.5068,0.10014,0.06405],"tcp_start":[0.50677,0.10007,0.06405],"tcp_to_object_dist_end":0.04606,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49651,0.07471,0.0247],"object_pos_start":[0.50763,0.12665,0.0264],"object_to_goal_dist_end":0.15551,"object_to_goal_dist_start":0.20724,"object_z_max":0.0342,"peak_contact_force":581.92254,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3964.0,"raw_peak_contact_force":718.86832,"subtask_id":"push","tcp_end":[0.51327,0.08,0.05768],"tcp_start":[0.5068,0.10014,0.06405],"tcp_to_object_dist_end":0.03737,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64912,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.07363,"approach_high.arc_height":0.27759,"approach_high.clearance_height":0.05171,"approach_high.speed":0.066,"contact_peg.contact_force":2.62483,"contact_peg.speed":0.03021,"push_through.push_distance":0.22514,"push_through.push_speed":0.04993,"push_through.push_tolerance":0.02441},"optimized_scores":{"best_composite_score":-0.01324,"best_fitness_score":0.24676,"best_task_score":0.33345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":816.0,"contact_point_centroid":[0.52508,0.03001,0.05991],"force_p95":498.07849,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":508.15799,"mean_force":402.15774,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50039,-0.03124,0.09561]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":248.0,"contact_point_centroid":[0.52503,0.11999,0.05995],"force_p95":424.06607,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.01494,"mean_force":340.37215,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49393,0.02577,0.11377]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":200.0,"contact_point_centroid":[0.47498,0.12,0.05996],"force_p95":292.37811,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.38378,"mean_force":160.62231,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49466,0.02369,0.11016]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":317.0,"contact_point_centroid":[0.47495,0.10057,0.05994],"force_p95":276.49524,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.76716,"mean_force":202.05479,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49086,0.02237,0.10716]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.47499,0.05562,0.05999],"force_p95":141.38152,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.33802,"mean_force":107.22484,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50034,-0.03108,0.09566]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.47499,0.12,0.05999],"force_p95":148.21705,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.0774,"mean_force":82.30556,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49885,-0.01979,0.09903]},{"body_a":"peg","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.50448,0.03896,0.06329],"force_p95":118.51065,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.67238,"mean_force":81.34405,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49596,-0.00745,0.10425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.50678,0.04995,0.00954],"force_p95":31.29398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.98678,"mean_force":6.82689,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.48964,0.02346,0.11462]},{"body_a":"peg","body_b":"link7","contact_count":346.0,"contact_point_centroid":[0.49888,0.07128,0.05955],"force_p95":53.78745,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.97031,"mean_force":13.48923,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49159,0.02233,0.10691]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52504,0.11998,0.05994],"force_p95":110.99359,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.99359,"mean_force":110.99359,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49166,0.03177,0.12241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.49997,-0.01398,0.00833],"force_p95":81.61756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.03608,"mean_force":12.10465,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49939,-0.0258,0.09771]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":109.0,"contact_point_centroid":[0.52508,0.01723,0.06],"force_p95":38.13263,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.72621,"mean_force":29.52223,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49691,-0.01299,0.10162]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,-0.04657,0.02421],"force_p95":7.28558,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.4985,"mean_force":2.41654,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49954,-0.0321,0.09595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48588,0.1071,0.24844]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5035,0.21498,0.29276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48976,0.03803,0.00938],"force_p95":0.54067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54067,"mean_force":0.54067,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49166,0.03177,0.12241]}],"total_contact_groups":16},"final_pose_error":0.157,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49556,-0.02249,0.02415],"final_tcp_position":[0.49882,-0.03334,0.09645],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":508.15799,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47866,0.02256,0.15462],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1285,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,0.04794,0.03378],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.12818,"object_to_goal_dist_start":0.14404,"object_z_max":0.03539,"peak_contact_force":371.28256,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1847.0,"raw_peak_contact_force":452.01494,"subtask_id":"approach","tcp_end":[0.49166,0.03177,0.12241],"tcp_start":[0.47866,0.02256,0.15462],"tcp_to_object_dist_end":0.09103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,0.04797,0.03378],"object_pos_start":[0.50469,0.04794,0.03378],"object_to_goal_dist_end":0.1282,"object_to_goal_dist_start":0.12818,"object_z_max":0.03378,"peak_contact_force":110.99359,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":110.99359,"subtask_id":"contact","tcp_end":[0.49153,0.0319,0.12243],"tcp_start":[0.49166,0.03177,0.12241],"tcp_to_object_dist_end":0.09105,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49556,-0.02249,0.02415],"object_pos_start":[0.50469,0.04797,0.03378],"object_to_goal_dist_end":0.05981,"object_to_goal_dist_start":0.1282,"object_z_max":0.04018,"peak_contact_force":484.9898,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2969.0,"raw_peak_contact_force":508.15799,"subtask_id":"push","tcp_end":[0.49882,-0.03334,0.09645],"tcp_start":[0.49153,0.0319,0.12243],"tcp_to_object_dist_end":0.07318,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```